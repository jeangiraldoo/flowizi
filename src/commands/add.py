from src.flowizi import flowizi


def add(args, parser):
    if args.w:
        website_name, website_link = args.w
        add_website(parser, args.name, website_name, website_link)
    elif args.f:
        file_url = args.f[0]
        file_name = file_url[file_url.rfind("/") + 1:]
        add_file(parser, args.name, file_name, file_url)
    else:
        add_environment(parser, args.name)


def add_environment(parser, env_name):
    if flowizi.json.exists_environment(env_name):
        parser.error("The environment specified already exists")

    flowizi.json.add_environment(env_name)
    print(f"The {env_name} environment has been added!")


def add_website(parser, env_name, name, url):
    if not flowizi.json.exists_environment(env_name):
        parser.error("The environment specified does not exist")

    if not flowizi.verify_URL(url, "website"):
        parser.error("The link does not follow a proper link format")

    for environment in flowizi.environment_list:
        website_exists = any(website.name == name for website in environment.websites)
        if environment.name == env_name and len(environment.websites) > 0 and website_exists:
            parser.error("This website already exists")

    website = create_website(name, url)
    flowizi.json.add_environment_element(env_name, "websites", website)
    print(f"The {name} website was added to the {env_name} environment")


def create_website(name, url):
    return {"name": name, "url": url}


def add_file(parser, env_name, name, url):
    if not flowizi.json.exists_environment(env_name):
        parser.error("The environment specified does not exist")

    if not flowizi.verify_URL(url, "file"):
        parser.error(
            "There's no file in your system associated"
            " with the path you typed"
        )

    for environment in flowizi.environment_list:
        file_exists = any(file.name == name for file in environment.files)
        if environment.name == env_name and len(environment.websites) > 0 and file_exists:
            parser.error("This file already exists")

    file = create_file(name, url)
    flowizi.json.add_environment_element(env_name, "files", file)
    print(f"The {name} in the {url} path was added to the {env_name} environment")


def create_file(name, url):
    return {"name": name, "url": url}
