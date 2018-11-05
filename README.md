Yubikey OTP for Alfred
======================

Easily retrieve OTP codes from your YubiKey device.

![Yubikey OTP for Alfred](https://raw.github.com/robertoriv/alfred-yubikey-otp/master/screenshot.gif)

## Requirements

Yubikey OTP for Alfred is a wrapper around [ykman](https://developers.yubico.com/yubikey-manager/).

To install `ykman`, use [Homebrew](https://brew.sh/):
```
brew install ykman
```

## Installation

1. Download the latest `Yubikey-for-Alfred.alfredworkflow` from the releases section.
2. Open it with `Alfred`.
3. Confirm that you want to install it.

## Usage

Set up a keyword for `Yubikey OTP for Alfred` by opening the workflow setting, double-clicking on the `Script Filter` input and filling in the keyword field (ex: `yfa`).

Launch `Alfred`, and type `yfa <some ifentifier>`. Once the desired entry shows up, hit `Enter` to copy it to your clipboard.

## Acknowledgements

`ykman`, `yubikey`, `Yubico Authenticator` and its icon are property of [Yubico](https://www.yubico.com/). **I am not affiliated with them, and this workflow is not officially vetted.**

I learned how to build this workflow by perusing the code for [alfred-homebrew](https://github.com/fniephaus/alfred-homebrew).

This workflow uses [alfred-workflow](https://github.com/deanishe/alfred-workflow).

All service icons belong to their respective owners.
