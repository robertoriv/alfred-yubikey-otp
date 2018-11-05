def get_icon_for_service(service):
    if "github" in service.lower():
        return "icons/github.png"

    if "aws" in service.lower() or "amazon web services" in service.lower():
        return "icons/aws.png"

    if "facebook" in service.lower():
        return "icons/facebook.png"
    
    if "google" in service.lower():
        return "icons/google.png"

    if "discord" in service.lower():
        return "icons/discord.png"

    if "dropbox" in service.lower():
        return "icons/dropbox.png"

    if "microsoft" in service.lower():
        return "icons/microsoft.png"

    if "wordpress" in service.lower():
        return "icons/wordpress.png"

    if "gitlab" in service.lower():
        return "icons/gitlab.png"

    return "icon.png"