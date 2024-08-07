# download OptimizedBark
wget https://github.com/gayanMatch/OptimizedBark/releases/download/release.0321/OptimizedBark_2024.0321.zip
unzip OptimizedBark_2024.0321.zip

# download TRT_Bark
wget https://github.com/gayanMatch/TRT_Bark/releases/download/release.0321/TRT_Bark_2024.03.21.zip
unzip TRT_Bark_2024.0321.zip

DOCKER_BUILDKIT=0 docker build -t tts-worker:release.0321 .
flyctl launch --org air-297 --vm-gpu-kind a100-pcie-40gb --local-only -i tts-worker:release.0321

