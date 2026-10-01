---
name: version-up
description: Used when there's a need to up version number. Triggered when user says he need to change version number.
---

## Version up workflow
[ ] Open `resource/version.yml`
[ ] Parse the YAML to find current version number (`version` key)
[ ] Increment the minor version of this value
[ ] Save the YAML file

## Gotchas
When the minor version number reaches 13, skip it and advance to 14
