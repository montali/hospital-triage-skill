from mycroft import MycroftSkill, intent_file_handler


class HospitalTriage(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('triage.hospital.intent')
    def handle_triage_hospital(self, message):
        reply = self.get_response(dialog='Quali sono i sintomi?',
                                  data=None, validator=None, on_fail=None, num_retries=-1)
        if self.voc_match(reply, 'fall'):
            self.handle_fall()
        elif self.voc_match(reply, 'headache'):
            self.handle_headache()
        # self.speak_dialog('triage.hospital')
        # self.converse(reply)

    def handle_fall():
        self.speak('Nemmeno a me piacciono le scale!')

    def handle_headache():
        self.speak('Lo studio ti frega')


def create_skill():
    return HospitalTriage()
