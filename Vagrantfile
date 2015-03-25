# Base Vagrant box for docker experiments
#   https://github.com/phusion/open-vagrant-boxes
   
VAGRANTFILE_API_VERSION = "2"
NAME = "gir-vm"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "phusion-open-ubuntu-14.04-amd64"
  config.vm.box_url = "https://oss-binaries.phusionpassenger.com/vagrant/boxes/latest/ubuntu-14.04-amd64-vbox.box"

  config.vm.network :forwarded_port, guest: 22, host: 2222, id: "ssh", disabled: true
  config.vm.network :forwarded_port, guest: 22, host: 5122, auto_correct: true
  config.vm.network :forwarded_port, guest: 80, host: 5180, id: "http"

  config.vm.provider :virtualbox do |vb|
    vb.name = NAME
  end

  if Dir.glob("#{File.dirname(__FILE__)}/.vagrant/machines/default/*/id").empty?
    # Install Docker
    pkg_cmd = "wget -q -O - https://get.docker.io/gpg | apt-key add -;" \
      "echo deb http://get.docker.io/ubuntu docker main > /etc/apt/sources.list.d/docker.list;" \
      "apt-get update -qq; apt-get install -q -y --force-yes lxc-docker; " \
      "curl -L https://github.com/docker/compose/releases/download/1.1.0/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose;" \
      "chmod +x /usr/local/bin/docker-compose;"
    # Add vagrant user to the docker group
    pkg_cmd << "usermod -a -G docker vagrant; "
    config.vm.provision :shell, :inline => pkg_cmd
  end
end
