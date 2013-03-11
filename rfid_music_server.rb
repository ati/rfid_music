require 'sinatra'
require 'socket'
#require 'uri'

set :port, 19000

def lms_play(card_id)
	id2album = {
		'88.34.51.F4' => 'Born%20To%20Die',
		'88.34.86.7A' => 'Anyone%20for%20Mozart%2C%20Bach',
		'88.34.72.DF' => 'Ballet%20music',
	}

	album = id2album[card_id]
	if ! album.nil?
		s = TCPSocket.new('localhost', 9090)
		s.print("playlist play db%3Aalbum.title%3D#{album}\n")
		s.print("exit\n")
		s.close
	end
end

#lms_play('88.34.86.7A')

get '/rfid/1/:card_id' do
  lms_play(params[:card_id])
  "ok"
end
