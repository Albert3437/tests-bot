sudo dnf update -y
sudo dnf install gcc gcc-c++ make python3-devel -y
sudo dnf install tmux -y
sudo yum install wget
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar xvzf ta-lib-0.4.0-src.tar.gz
cd ta-lib
./configure --prefix=/usr
make
sudo make install
cd ..
pip install -r requirements.txt