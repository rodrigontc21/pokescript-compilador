# Programa valido em PokeScript
# Demonstra: declaracao, atribuicao, condicional, laco e saida

pokemon dragonite
    nivel  = 55
    hp     = 180
    ataque = 134
fim

capturar nomeRival

enquanto dragonite.hp > 0 faca
    se dragonite.ataque > 100 e dragonite.nivel >= 50 entao
        dano = dragonite.ataque * 2
        mostrar "Dragonite usou Hiperrayo em " + nomeRival + "!"
        mostrar dano
        dragonite.hp = dragonite.hp - 10
    senao
        mostrar "Dragonite esta cansado..."
        dragonite.hp = 0
    fim
fim

mostrar "Batalha encerrada!"
