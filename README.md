# battdvr
An automated script to manage television episodes like a DVR.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Installing

- Use Python 3. If you don't have it, visit [python.org](https://www.python.org/downloads/)
- Git clone [this repo]() to correct directory  
    `git clone https://github.com/mvbattista/battdvr.git battdvr`
- Create a virtual environment  
    `pip install virtualenv`  
    `cd <path_to_project_dir>`  
    `virtualenv battdvr`
- Install required python libraries from [requirements.txt](/requirements.txt)  
    `sudo pip install -r requirements.txt`
- Set up a config file in `~/.config/battdvr/config` using [config_sample](/config_sample)
- Run the script  
    `python battdvr.py`

<!--
## Running the tests

Explain how to run the automated tests for this system

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds
-->
## Contributing

Feel free to submit a pull request if you have code ready to be merged, or submit an issue for bugs and improvements.

<!--
## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors

* **Billie Thompson** - *Initial work* - [PurpleBooth](https://github.com/PurpleBooth)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.
-->

## License

This project is licensed under the Unlicense - see the [LICENSE.md](/LICENSE.md) file for details

<!--## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc-->


## TODO
-	Add Nickelodeon, Discovery, Cartoon Network (adult swim), Crackle, Comedy Central, TBS, et. al
- Add network level video concatenation
- Check mounted network drive and automatically mount
- Setup in automation (possibly with [ndscheduler](https://github.com/Nextdoor/ndscheduler))
