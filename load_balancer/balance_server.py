from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
import redis
import uuid
import json
import time
import base64
import uvicorn
import os
from datetime import datetime, timezone
from google.cloud import storage
from autoscaler import Monitor
# from pymongo import MongoClient

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "voice-npz.json"
app = FastAPI()
redis_url = os.environ.get(
    "redis_url",
    'redis://default:eb7199cbf0f54bf5bb084f7f1d594692@fly-bark-queries.upstash.io:6379'
)
# mongo_uri = os.environ.get(
#     "mongo_uri",
#     "mongodb+srv://ginger:P%40ssw0rd131181@bark-log.1fit2mh.mongodb.net/?retryWrites=true&w=majority&appName=bark-log"
# )
# client = MongoClient(mongo_uri)
r_sub = redis.Redis.from_url(redis_url)
# r_sub = redis.Redis(
#   host='localhost',  # Changed to localhost
#   port=6379,
#   password=''  # Likely no password if you're just testing locally
# )
r_pub = redis.Redis.from_url(redis_url)
r_monitor = redis.Redis.from_url(redis_url)
monitor = Monitor(r_monitor)
monitor.start()
r_pub.setnx('active_requests', 0)

# r_pub = redis.Redis(
#   host='localhost',  # Changed to localhost
#   port=6379,
#   password=''  # Likely no password if you're just testing locally
# )

def get_prediction_stream(request_id):
    """Yields prediction data in real-time."""
    # Subscribe to Redis channel for real-time predictions
    pubsub = r_sub.pubsub()
    pubsub.subscribe(request_id)

    for message in pubsub.listen():
        # Check for message type to avoid initial subscription confirmation message
        if message['type'] == 'message':
            data = message['data']
            # Assuming the 'complete' signal is a message with '{"complete": true}'
            if b'complete' in data:
                break
            encoded_result = json.loads(data)['prediction']
            decoded_result = base64.b64decode(encoded_result)
            yield decoded_result


def check_voice(voice):
    client = storage.Client()

    # Get the bucket
    bucket = client.get_bucket('tts-voices-npz')
    blob = bucket.blob(voice + ".npz")
    return blob.exists()


@app.post("/{call_id}/synthesize", response_class=StreamingResponse)
async def predict(call_id: str, request: Request):
    request_id = str(uuid.uuid4())
    data = await request.json()
    text = data.pop("text")
    voice = data.pop("voice").replace('.npz', '')
    rate = data.pop("rate") if "rate" in data.keys() else 1.0
    if not check_voice(voice):
        def stream_results():
            yield f"NO VOICE {voice}"

        return StreamingResponse(stream_results(), status_code=400)
    r_pub.lpush(
        "ml_requests",
        json.dumps(
            {
                "request_id": request_id,
                "text": text,
                "voice": voice,
                "rate": rate,
                "request_time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")
            }
        )
    )
    r_pub.incr('active_requests')

    def event_stream():
        return get_prediction_stream(request_id)

    return StreamingResponse(event_stream(), media_type="application/octet-stream")


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5000,
        log_level="debug",
    )
