require 'rubygems' if RUBY_VERSION < "1.9"
require 'sinatra'
require 'socket'
use Rack::Logger
require 'open-uri'

class RfidMusicServer < Sinatra::Base
	# set :port, 19000 # set it in config.ru

	MUSIC_CONFIG_FILENAME = '/WD15EARS/share/music/rfid_music.cfg'

	def self.read_music_config
		res = {}
		IO.foreach(MUSIC_CONFIG_FILENAME) do |line|
			n, card_id, album_title = line.strip.split(/,/, 3)
			res[card_id.strip] = album_title.to_s.strip unless card_id.nil?
		end
		return res
	end

	def card_to_album(card_id)
		LOGGER.info("converting card_id = #{card_id} to album title")

		# try to find a match for partial card_id
		albums = settings.music_config.keys.grep(Regexp.new(Regexp.escape(card_id)))
		if albums.count.eql?(1)
			album = albums.first
			return album.empty? ? "Please configure card #{card_id}" : settings.music_config[album]
		else
			return "Unknown card: #{card_id}"
		end
	end


	def lms_play(album)
		LOGGER.info("Trying to play album '#{album}'")

		if ! album.nil?
			album_uri = URI::encode(album)
			s = TCPSocket.new('localhost', 9090)
			s.print("playlist play db%3Aalbum.title%3D#{album_uri}\n")
			s.print("exit\n")
			LOGGER.info("playlist play db%3Aalbum.title%3D#{album_uri}\n")
			s.close
		end
	end


	get '/rfid/1/:card_id' do
	  lms_play(card_to_album(params[:card_id].strip))
	  "ok"
	end


	configure do
		LOGGER = Logger.new(STDOUT)
		enable :logging, :dump_errors
		set :raise_errors, true

		LOGGER.info("Loading config")
		set :music_config, RfidMusicServer::read_music_config
	end
end
