import can

class Listener(can.Listener):
    def on_message_received(self, msg):
        print(msg)
        print('writing to file')
        fileObject = open('data.txt', 'w')
        fileObject.write(str(msg))
        fileObject.write("SUCCCESS")
        fileObject.close()