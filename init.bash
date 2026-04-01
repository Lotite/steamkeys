sudo apt update && sudo apt upgrade -y
sudo apt install -y wget curl unzip libnss3 libgbm1 libasound2


sudo apt install docker.io -y
sudo usermod -aG docker $USER


wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
bash miniconda.sh -b -p $HOME/miniconda3
rm miniconda.sh

source "$HOME/miniconda3/etc/profile.d/conda.sh"
conda init bash

chmod +x chromeInstaler.bash
./chromeInstaler.bash

conda env create -f environment.yml


