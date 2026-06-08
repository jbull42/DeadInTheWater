# Dead In The Water

## Description
Dead In The Water is a top-down WWII naval combat game built with Python and pygame. 
The player controls a WWII warship, manages the ship's ammo, and must target and destroy enemy ships both within and beyond visual range.

## How to Run
After cloning the repository onto your machine, navigate to the main directory and run the following commands:
source venv/bin/activate  
python3 main.py

## Controls
| Key | Action |
| --- | ------ |
| W / S | Forward / Reverse |
| A / D | Left / Right |
| &larr; / &rarr; | Rotate Turret |
| &darr; / &uarr; | Raise / Lower Turret |
| T | Fire Torpedo (if equipped) |
| click radar screen | select target |
| Esc | Quit Game |
| R | Restart Game (once level completed) |

## Features
Each ship is equipped with its own loadout of shells, each shell providing a different amount of damage and armor-piercing capability. 
The radar screen allows the player to target and engage ships beyond visual range. The player can click on an enemy ship on the radar screen and 
manually aim the provided indicator, and the fire control system will calculate the enemy ship's distance and direction and provide the player with 
the optimal turret elevation angle to maximize the chance of hitting the target. Enemy ships can be programmed to follow distinct
waypoints and firing schedules, and difficulty can be controlled by adjusting the accuracy of the enemy's fire control systems.

## Requirements
Python 3.11  
pygame 2.6.1

