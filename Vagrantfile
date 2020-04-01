# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  config.vm.box = "ubuntu/xenial64"
  config.vm.network "private_network", ip: "192.168.34.34"
  config.vm.synced_folder "./", "/var/www/html/", id: "vagrant-root", :group=>'www-data', :mount_options=>['dmode=775,fmode=775']
  config.vm.provision :shell, path: "bootstrap.sh"

  config.vm.define :LuckyTrack do |t|
  end

  config.vm.provider "virtualbox" do |v|
    v.memory = 1048
    v.cpus = 1
  end

end
