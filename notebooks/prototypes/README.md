# Jupyter notebooks

Jupyter notebooks for support of NEANIAS Space-Planetary analysis.

The notebooks here are run -- for convenience -- using a Docker container,
`chbrandt/gispy:gdal-jupyter` @ Docker-Hub.

To run it:
```bash
$ docker run --name gispy -p 8888:8888 -it \
         -v $PWD/notebooks:/mnt/notebooks  \
         chbrandt/gispy:gdal-jupyter
```

-----
Note:

* So far, the packages are not versionized neither is the container.
  * TODO: bind notebooks to specific version of container and/or packages (environment).

## ToC

* [ODE REST API](ode_rest_api.md)
