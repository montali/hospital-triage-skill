# <img src="https://raw.githack.com/FortAwesome/Font-Awesome/master/svgs/solid/hospital-user.svg" card_color="#40DBB0" width="50" height="50" style="vertical-align:bottom"/> Hospital Triage

Help ER patients by understanding why they're there.

## About

This skill was born to help er patients on their arrival at the hospital. It asks the patient basic questions about his health.

### How it works

The skill is activated by saying the wake word (which, by default is `hey mycroft` but will be changed) and asking help:

`Hey Mycroft, puoi aiutarmi?`

Then, the interaction begins: the bot asks if it's talking directly with the patient. This helps us understands if he/she's conscious. Then, it asks about the main symptom. Right now, it recognises:

* Faints
* Hemorrhages
* Shocks
* Breathing difficulties
* Fractures (extracting the affected limb)
* Fevers
* Burns
* Abdominal pains

If the declared symptom is compatible with the COVID19, the bot asks some questions to determine the `covid_score`, an index determining how likely the patient is affected by COVID19.

It then assigns the patient a color code, according to the CESIRA index, and asks him/her to quantify the pain. Finally, it asks the patient his/her age and creates a `med_record` object containing all the gathered informations. This `med_record` can then be exported to assist the doctor during the checks.

## How to use

Remember to disable `personal` skill by adding `"mycroft-personal.mycroftai"` to the blacklisted list in `mycroft-core/mycroft/configuration/mycroft.conf`.

To install this skill, you just have to clone this repo inside of `/opt/mycroft/skills`

## Defining new symptoms

Each symptom is defined by:

* Its intent file, containing the triggering phrases used to train the model. `locale/[LANG]/symptoms.[name].intent`
* Its dialog file, containing the bot's responses. `locale/[LANG]/symptoms.[name].dialog`
* A handler, decorated with `@intent_file_handler` and `@symptom_handler`

If it is a COVID19-compatible symptom, it is decorated with `@covid_symptom` too.

For example, the *short breath* handler is this:

```python
# BREATH
@intent_file_handler('symptoms.breath.intent')
@symptom_handler
@covid_symptom
def handle_breathing(self, message):
  self.med_record["main_symptom"] = "breathing"
  self.med_record["code"] = "red"
  self.speak_dialog('symptoms.breath')
```



## Triggering phrases

- "Ho bisogno di una visita"
- "Non mi sento bene"
- "Ho bisogno di aiuto"
- "Mi serve un medico"
- "Non sto bene"
- "Sto male"
- "Ho dei dolori"
- "Puoi aiutarmi"

## Credits

montali

## Category

**Information**

## Tags

#Hospital
#Triage
#Health
#Er
