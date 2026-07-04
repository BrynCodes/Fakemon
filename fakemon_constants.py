from pathlib import Path

WIDTH, HEIGHT = 1280, 720
AssetsPath = Path('Assets')
FontPath = AssetsPath / 'Misc'/'PixelPurl.ttf'

weakness = {
    "null": {
        0: [],
        0.5: [],
        1: ["normal", "fighting", "flying", "poison", "ground", "rock", "bug", "ghost", "steel", "fire", "water",
            "grass", "electric", "psychic", "ice", "dragon", "dark", "fairy"],
        2: []
    },

    "???": {
        0: ["???"],
        0.5: ["normal"],
        1: [],
        2: ["fighting", "flying", "poison", "ground", "rock", "bug", "ghost", "steel", "fire", "water", "grass",
            "electric", "psychic", "ice", "dragon", "dark", "fairy"],
    },

    "normal": {
        0: ["ghost", "???"],
        0.5: ["rock", "steel"],
        1: ["normal", "fighting", "flying", "poison", "ground", "bug", "fire", "water", "grass", "electric", "psychic",
            "ice", "dragon", "dark", "fairy"],
        2: [0]
    },

    "fighting": {
        0: ["ghost", "???"],
        0.5: ["flying", "poison", "bug", "psychic", "fairy"],
        1: ["fighting", "ground", "fire", "water", "grass", "electric", "dragon"],
        2: ["normal", "rock", "steel", "ice", "dark"]
    },

    "flying": {
        0: ["???"],
        0.5: ["rock", "steel", "electric"],
        1: ["normal", "flying", "poison", "ground", "ghost", "fire", "water", "psychic", "ice", "dragon", "dark",
            "fairy"],
        2: ["fighting", "bug", "grass"]
    },

    "poison": {
        0: ["steel", "???"],
        0.5: ["poison", "ground", "rock", "ghost"],
        1: ["normal", "fighting", "flying", "bug", "fire", "water", "electric", "psychic", "ice", "dragon", "dark"],
        2: ["grass", "fairy"]
    },

    "ground": {
        0: ["flying", "???"],
        0.5: ["bug", "grass"],
        1: ["normal", "fighting", "ground", "ghost", "water", "psychic", "ice", "dragon", "dark", "fairy"],
        2: ["poison", "rock", "steel", "fire", "electric"]
    },

    "rock": {
        0: ["???"],
        0.5: ["fighting", "ground", "steel"],
        1: ["normal", "poison", "rock", "ghost", "water", "grass", "electric", "psychic", "dragon", "dark", "fairy"],
        2: ["flying", "bug", "fire", "ice"]
    },

    "bug": {
        0: ["???"],
        0.5: ["fighting", "flying", "posion", "ghost", "steel", "fire", "fairy"],
        1: ["normal", "ground", "rock", "bug", "water", "electric", "ice", "dragon"],
        2: ["grass", "psychic", "dark"]
    },

    "ghost": {
        0: ["normal", "???"],
        0.5: ["dark"],
        1: ["fighting", "flying", "poison", "ground", "rock", "bug", "steel", "fire", "water", "grass", "electric",
            "ice", "dragon", "fairy"],
        2: ["ghost", "psychic"]
    },

    "steel": {
        0: ["???"],
        0.5: ["steel", "fire", "water", "electric"],
        1: ["normal", "fighting", "flying", "poison", "ground", "bug", "ghost", "grass", "psychic", "dragon", "dark"],
        2: ["rock", "ice", "fairy"]
    },

    "fire": {
        0: ["???"],
        0.5: ["rock", "fire", "water", "dragon"],
        1: ["normal", "fighting", "flying", "poison", "ground"],
        2: ["bug", "steel", "grass", "ice"]
    },

    "water": {
        0: ["???"],
        0.5: ["water", "grass", "dragon"],
        1: ["normal", "fighting", "flying", "poison", "bug", "ghost", "steel", "electric", "psychic", "ice", "dark",
            "fairy"],
        2: ["ground", "rock", "fire"]
    },

    "grass": {
        0: ["???"],
        0.5: ["flying", "poison", "bug", "steel", "fire", "grass", "dragon"],
        1: ["normal", "fighting", "ghost", "electric", "psychic", "ice", "dark", "fairy"],
        2: ["ground", "rock", "water"]
    },

    "electric": {
        0: ["ground", "???"],
        0.5: ["grass", "electric", "dragon"],
        1: ["normal", "fighting", "poison", "rock", "bug", "ghost", "steel", "fire", "psychic", "ice", "dark", "fairy"],
        2: ["flying", "water"]
    },

    "psychic": {
        0: ["dark", "???"],
        0.5: ["steel", "psychic"],
        1: ["normal", "flying", "ground", "rock", "bug", "ghost", "fire", "water", "grass", "electric", "ice", "dragon",
            "fairy"],
        2: [0]
    },

    "ice": {
        0: ["???"],
        0.5: ["steel", "fire", "water", "ice"],
        1: ["normal", "fighting", "poison", "rock", "bug", "ghost", "electric", "psychic", "dark", "fairy"],
        2: ["flying", "ground", "grass", "dragon"]
    },

    "dragon": {
        0: ["fairy", "???"],
        0.5: ["steel"],
        1: ["normal", "fighting", "flying", "poison", "ground", "rock", "bug", "ghost", "fire", "water", "grass",
            "electric", "psychic", "ice", "dark"],
        2: ["dragon"]
    },

    "dark": {
        0: ["???"],
        0.5: ["fighting", "dark", "fairy"],
        1: ["normal", "flying", "poison", "ground", "rock", "bug", "steel", "fire", "water", "grass", "electric", "ice",
            "dragon"],
        2: ["ghost", "psychic"]
    },

    "fairy": {
        0: ["???"],
        0.5: ["poison", "steel", "fire"],
        1: ["normal", "flying", "ground", "rock", "bug", "ghost", "water", "grass", "electric", "psychic", "ice",
            "fairy"],
        2: ["fighting", "ice", "dark"]
    },
}

fakemon_locations = {
    'plain': ['Zangoose', 'Manectric', 'Mightyena', 'Flygon', 'Tropius'],
    'jungle': ['Sceptile', 'Breloom', 'Venomoth', 'Shiftry', 'Arbok'],
    'snowy': ['Glalie', 'Walrein', 'Sealeo', 'Delibird', 'Sneasel'],
    'beach': ['Wailmer', 'Pelipper', 'Corsola', 'Whiscash', 'Lanturn']

}
