from goprohero4 import GoProHero4

camera = GoProHero4()

status = camera.status()

#print status
camera.command('mode', 'video')
camera.command('fps', 2)

#print status
