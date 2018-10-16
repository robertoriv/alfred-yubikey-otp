def get_icon_for_service(service):
    if "github" in service.lower():
        return "icons/GitHub-Mark-64px.png"

    if "aws" in service.lower() or "amazon web services" in service.lower():
        return "icons/aws.png"
    
    return "icon.png"