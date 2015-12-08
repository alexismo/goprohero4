from goprohero4 import GoProHero4

camera = GoProHero4()

status = camera.status()

if( status["state"]["current_mode"] == "photo"):
    camera.command('mode', 'multishot')
    print "changed mode to multishot"
else:
    camera.command('mode','photo')
    print "changed mode to photo"
