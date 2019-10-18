def get_icon_for_service(service):
    if "github" in service.lower():
        return "icons/github.png"

    if "aws" in service.lower() or "amazon web services" in service.lower():
        return "icons/aws.png"

    if "bitbucket" in service.lower():
        return "icons/bitbucket.png"

    if "discord" in service.lower():
        return "icons/discord.png"

    if "dropbox" in service.lower():
        return "icons/dropbox.png"

    if "electronic arts" in service.lower():
        return "icons/electronic_arts.png"

    if "facebook" in service.lower():
        return "icons/facebook.png"

    if "firefox" in service.lower():
        return "icons/firefox.png"

    if "gitlab" in service.lower():
        return "icons/gitlab.png"
    
    if "google" in service.lower():
        return "icons/google.png"

    if "heroku" in service.lower():
        return "icons/heroku.png"

    if "instagram" in service.lower():
        return "icons/instagram.png"

    if "microsoft" in service.lower():
        return "icons/microsoft.png"

    if "openvpn" in service.lower():
        return "icons/openvpn.png"

    if "wordpress" in service.lower():
        return "icons/wordpress.png"

    return "icon.png"