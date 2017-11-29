# urgentcare
Lamba code for Alexa Skill for locating closest Urgent Care Facility

This is pretty useless for most people.  This is how I did my code which is running on lambda for this Alexa Skill.  It could be easily tweaked to provide similar interactions between multiple points.

It works by taking the device ID and api Authorization Token from an Alexa device in order to obtain the device's registered location.  Said registered location is then fed to google Maps APIs (geocode/Travel Time).  It returns the clinic with the lowest travel time.  It then polls a waiting room API for wait time of that designated clinic.

I've sanitized out a bunch of shit.  Don't expect to copy/paste this into lambda and have a working app.
