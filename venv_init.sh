sudo apt install python3-pip
sudo pip install virtualenv
sudo pip install virtualenvwrapper
echo export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3 >> .zshrc
echo export WORKON_HOME=$HOME/.virtualenvs >> .zshrc
echo export PROJECT_HOME=$HOME/dev >> .zshrc
echo source /usr/local/bin/virtualenvwrapper.sh >> .zshrc
