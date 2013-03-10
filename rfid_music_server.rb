require 'sinatra'

get '/rfid/1/:card_id' do
  printf("%x", params[:card_id])
  "ok"
end
