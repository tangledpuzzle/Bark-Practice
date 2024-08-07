import os
import invoke

c = invoke.Context()


class Commands:
    def __init__(self):
        self.token = os.getenv("FLY_TOKEN")
        if not self.token:
            raise Exception("FLY_TOKEN is required")

    def count(self, *, a=None, state=None):
        """shows the number of machines"""
        app_name = a
        if not app_name:
            return print("App name is required")

        result = self.get_machines_by_state(a=app_name, state=state)
        result = c.run(
            f'echo "{result}" | awk "NF" | wc -l',
            echo=False,
            hide="both",
            warn=True,
        )
        count = int(result.stdout)
        return count

    def stop(self, *, a=None, count=None):
        """stop `count` number of started machines"""
        app_name = a
        if not app_name:
            return print("App name is required -a")

        if not count:
            return print("Count of machines to stop is required --count")

        started_machine_ids = self.get_machines_by_state(a=app_name, state="started")
        result = c.run(
            f"echo \"{started_machine_ids}\" | awk 'NF' | head -n {count} | xargs -P 0 -L 1 -I {{id}} flyctl m stop {{id}} -a {app_name} -t {self.token}"
        )

    def start(self, *, a=None, count=None):
        """start `count` number of stopped machines"""
        app_name = a
        if not app_name:
            return print("App name is required -a")

        stopped_machine_ids = self.get_machines_by_state(a=app_name, state="stopped")
        result = c.run(
            f"echo \"{stopped_machine_ids}\" | awk 'NF' | head -n {count} | xargs -P 0 -L 1 -I {{id}} flyctl m start {{id}} -a {app_name} -t {self.token}"
        )

    def add(self, *, a=None, count=None):
        """clone `count` number of machines"""
        app_name = a
        if not app_name:
            return print("App name is required -a")

        if not count:
            return print("Count of machines to add is required --count")

        result = c.run(
            f"flyctl m list -q -a {app_name} -t {self.token} | awk 'NF' | head -n {count}"
        )
        images = result.stdout.strip()
        result = c.run(
            f"yes '{images}' | head -n {count} | xargs -P 0 -L 1 -I {{id}} flyctl m clone {{id}} -a {app_name} -t {self.token}"
        )

    def remove(self, *, a=None, count=None):
        """destroys `count` number of stopped machines"""
        app_name = a
        if not app_name:
            return print("App name is required -a")

        if not count:
            return print("Count of machines to destroy is required --count")

        stopped_machine_ids = self.get_machines_by_state(a=app_name, state="stopped")
        result = c.run(
            f"echo \"{stopped_machine_ids}\" | awk 'NF' | head -n {count} | xargs -P 0 -L 1 -I {{id}} flyctl m destroy {{id}} -a {app_name} -t {self.token}"
        )

    def stop_machine(self, *, a=None, machine_id=None):
        app_name = a
        if not app_name:
            return print("App name is required -a")

        if not machine_id:
            return print("machine_id to stop is required --count")

        c.run(f"flyctl m stop {machine_id} -a {app_name} -t {self.token}")

    def get_machines_by_state(self, *, a=None, state=None):
        """get machines from app by state"""
        app_name = a
        if not app_name:
            return print("App name is required -a")

        if not state:
            result = c.run(
                f"flyctl m list -a {app_name} -t {self.token} --json | jq -r '.[] | .id' | awk 'NF'",
                echo=False,
                warn=True,
                hide="out",
            )
            if result.stderr:
                raise Exception(result.stderr)
            return result.stdout

        opts = dict(
            echo=False,
            warn=True,
            hide="out",
        )
        # Uncomment to debug
        # if state == "started":
        #     opts = dict()

        result = c.run(
            f"flyctl m list -a {app_name} -t {self.token} --json | jq -r '.[] | select(.state == \"{state}\") | .id' | awk 'NF'",
            **opts,
        )

        # Uncomment to debug thrashing
        # if state == "started":
        #     print(result)

        if result.stderr:
            raise Exception(result.stderr)
        return result.stdout
