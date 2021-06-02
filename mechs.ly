


Workspace "Battle"
Schema
    "BattleManager"
        has pRNG

    "BattleMech"
        has Ints ["stress", "reactor_limit", "heat", "heatGauge"]
        has Team "team"
        has Bools ["frontline", "backline"]
        has Lists.Card ["hand", "deck", "discard"]
    
    "Distance" is Int

    "Card"
        has Statblock "stats"
        has Action "playEffect"
        has \Action -> Bool\ "canReact"

    "Range"
        immutable
        has Bools ["Melee", "Close", "Mid", "Long"]

    "Statblock"
        immutable
        has Ints ["hull", "agi", "cpu", "bias"]
    
Functions
    Range "covers" Distance -> Bool
        distance 0 => melee or close range
        distance 1 => mid range
        distance 2 => long range

    Statblock "+" Statblock 
        Statblock with sum of each field
    eg. (Statblock 1 2 3 4) + (Statblock 10 10 10 10) 
            -> (Statblock 11 12 13 14)
    
    Statblock "dotProduct" Statblock
        sum of products of each field
    eg. (Statblock 1 2 3 4) + (Statblock 1 0 2 0) -> 7

    "Parse" String -> Statblock

        each "token" from string.split {

            if isdigit { 
                bias = token as int
                continue
            }

            if starts with '-' {
                sign = -1 (default 1)
                remove first character
            }

            if starts with regex '\d\*' {
                amount = first character as int (default 1)
                remove first 2 characters
            }

            match token {
                'HULL' => Hull
                'AGI'  => Agi
                'CPU'  => Cpu
            }

            set to sign*amount
        }



"Parse" String -> (StatBlock "result")
    replace all '+'s with spaces
    split on spaces

    each "token" {
        extract "{Integer}?{HULL|AGI|CPU}?"
        set result field
    }

:: Tests












digit |> set bias, continue
starts with minus_sign |> sign to -1
starts with regex '\d\*' |> 










=== Script "GuessingGame"

using ConsoleIO, Random

validRange = 1..100
secret = random from validRange

guesses down to 6 {
    choice = askfor Integer in validRange

    match comparison {
        greater => print 'Too high.'
        lesser  => print 'Too low.'
        equal   => print 'You win!', break
    }
}


=== Script "Euler1"

Integer "multiple" of:Integer
    mod equals 0
eg. `9 multiple of 3` -> True
    `3 multiple of 9` -> False

multiples of 3 or 5
eg. from 1 to 10 -> [3, 5, 6, 9]
    sum from 1 to 10 -> 23

sum from 1 to 1000