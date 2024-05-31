# CXVIZ: Data Visualization for CAIXA Investment Funds

## Introduction
This project is an enhanced Data Visualization for [CAIXA Investment Funds](https://www.fundos.caixa.gov.br/sipii/pages/public/listar-fundos-internet.jsf).

It served mostly for learning Python GUI with tkinter.

It uses [PhantomJS](https://phantomjs.org/) to access [CAIXA Investment Funds](https://www.fundos.caixa.gov.br/sipii/pages/public/listar-fundos-internet.jsf) webpage and download content available there.

## Installation
- Requirements:
    - python >= 3.8.10
    - python3-tk >= 3.8.10
    - python3-pil >= 7.0.0
    - python3-pil.imagetk >= 7.0.0
    - phantomjs >= 2.1.1
    - matplotlib >= 3.5.1
    - numpy >= 1.21.5

- After installing the dependencies, run:

```
python3 cxviz config <PHANTOMJS_INSTALL_PATH>
```

where PHANTOMJS_INSTALL_PATH is the install directory for PhantomJS (without including `bin`).

## Running
Run `cxviz feed` to automatically download updates from [CAIXA Investment Funds page](https://www.fundos.caixa.gov.br/sipii/pages/public/listar-fundos-internet.jsf) and plot the charts.

```
python3 cxviz feed
```

TODO: Set the funds and metrics to be automatically plotted in the `.cxviz` configuration file

## License
See the LICENSE file for license rights and limitations (GPL-3.0).
Icon by [MCruz (WMF)](https://commons.wikimedia.org/wiki/User:MCruz_(WMF)) available at https://commons.wikimedia.org/wiki/File:Growth_icon.svg under CC BY-SA 4.0 Deed Attribution-Share Alike 4.0 International license.
