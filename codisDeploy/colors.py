#!/home/tops/bin/python
#****************************************************************#
# ScriptName: colors.py
# Author: LeiChengliang
# Create Date: 2017-10-14 13:25
# Modify Author: 
# Modify Date: 2017-10-14 15:14
# Function: colors
#***************************************************************#
class colors():
    '''convert the color code  to word!'''
    end = '\033[0m'
    color = {'green':'\033[92m','bule':'\033[94m','yellow':'\033[93m','red':'\033[91m','bold':'\033[1m','underline':'\033[4m'}
    def test(self):
        word='color'
        for k,v in self.color.items():
            print(k + ':' + v + word + self.end)		
if __name__ == '__main__':
    colors().test()