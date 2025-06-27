# HumanInteractionSimulator: branch: world

This branch related purely to world generation.

Idea is to have a "world" with a certain fixed amount of _resources_.

These resources are distributed according to region.

E.g., some regions, particularly jungles may have a greater diversity of animal species (however whether or not animal species are important in this simulation is yet to be discussed).

Moreover, they may be rich in terms of resources like land cultivatability, wood, food, etc. However, being jungles they may also pocess characteristics that agents may want to be vary of, namely the presence of predators/toxic/poisonous creatures.

## Layers of Creation

Still, while _region_ is definitely a layer, these layers are created only after the primarly layers are created.

Thus, creation shall be distributed along multiple layers. Here are some preliminary ideas for the relevant layers:

### Land Masses

This one places continents across an initially neverending ocean.

Parameters to consider:

- Size
- Shape
- Number of continents
- Formation of smaller land masses like islands, etc.

### Topology

This one concerns itself with the numerous surface level details on the map. The idea of having slopes, trenches, plateaus, etc. are all to be considered under this one.
Topology, as well as the prevalence of water bodies, rainfall, temperature is bound to decide the type, quantity and diversity of species that shall inhabit patches of land.

### Weather and Water Bodies

This one is still developing. It might very well be that this one merges with some of the other ideas (more true for the Water Bodies than the weather), but here it is for now.
Most of the weather shall be determined by latitude, distance from ocean, altitude, etc. factors.

READUP:
Some readup shall be required when trying to understand rain patters and why deserts form and why it doesn't rain much over there. This might be related to the physical obstructions present on the land mass, i.e., the Western Ghats being higher up in altitude cause rain clouds to rise up over them, resulting in a decrease in surrounding pressure causing the relatively higher pressure clouds to release water due to the pressure imbalance (this may not be entirely true), however, there are plenty of land masses where it rains quite often without any action by mountains.

_Water bodies_ will be linked to rainfall, rivers will be linked to the flow of water from higher altitude to lower (also based on rainfall). Perennial rivers will be linked to snow.


### Vegetation and Animals

Once the land masses have been setup and made suitable for life, greenly will be prompty added.
Elevation, temperature, rainfall, climate will determine the type, quantity and diversity of vegetation.

Animals will be associated with certain kinds of vegetation and environment as well. E.g., animals that live in the snow, tropical ones. These include mammals, birds, reptiles and also insects, amphibians, etc.

### Humans

Finally, with the experiment setup, agents will be randomly spawned at equal distances. They will then begin to interact. Races might be considered and will shape the way humans view each other.

Other complicated features like language, etc. will develop as a result of social interaction. Socially isolated groups may not share many characteristics in terms of language. On the other hand, connected land masses may still present dialects of the same tongue. These will again play some role in the way a human sees another.


### Representation of these characteristics

Key thing to note is that this world isn't particularly keen on rendering things for the sake of presentation. Most of these factors will be represented with numbers.

Topology might be the represented via intermediate markers in a location: height format.

Rivers could be an array of points which when connected would form the river. However, the river may also have a certain thickness... this may be implemented at a later stage.

There are going to be a lot, lot of data structures and so many attributes.

Thank you, hope you like it :)
