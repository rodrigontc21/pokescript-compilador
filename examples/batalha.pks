# PokeScript - Exemplo completo: Batalha Pokemon
# Demonstra: pokemon, batalha, se/senao, enquanto, mostrar, capturar

pokemon dragonite
    nivel  = 55
    hp     = 250
    ataque = 134
    defesa = 90
fim

pokemon charizard
    nivel  = 52
    hp     = 210
    ataque = 122
    defesa = 80
fim

mostrar "=== BEM-VINDO AO POKESCRIPT ARENA ==="
mostrar "Treinador, qual o seu nome?"
capturar treinador

mostrar "Preparando batalha..."

batalha dragonite vs charizard faca
    mostrar "Vez do Dragonite!"
    dano_drag = dragonite.ataque - charizard.defesa
    se dano_drag < 10 entao
        dano_drag = 10
    fim
    charizard.hp = charizard.hp - dano_drag
    mostrar "Dragonite causou " + dano_drag + " de dano!"
    mostrar "Charizard HP restante: " + charizard.hp

    mostrar "Vez do Charizard!"
    dano_char = charizard.ataque - dragonite.defesa
    se dano_char < 10 entao
        dano_char = 10
    fim
    dragonite.hp = dragonite.hp - dano_char
    mostrar "Charizard causou " + dano_char + " de dano!"
    mostrar "Dragonite HP restante: " + dragonite.hp

    se dragonite.hp > charizard.hp entao
        mostrar "Dragonite esta vencendo!"
    senao
        mostrar "Charizard esta vencendo!"
    fim
fim

mostrar ""
mostrar "=== RESULTADO FINAL ==="
mostrar "Treinador: " + treinador

se dragonite.hp > 0 e charizard.hp <= 0 entao
    mostrar "DRAGONITE VENCEU!"
senao
    se charizard.hp > 0 e dragonite.hp <= 0 entao
        mostrar "CHARIZARD VENCEU!"
    senao
        mostrar "EMPATE EPICO!"
    fim
fim

mostrar "HP Dragonite: " + dragonite.hp
mostrar "HP Charizard: " + charizard.hp
