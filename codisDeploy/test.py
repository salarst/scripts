import yaml

fd = open('resources/main.conf')
y = yaml.load(fd)
p = y['DeployPath']
print(p)
for i in p.values():
    print(i)