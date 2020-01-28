package sockets

//Contact defines required functions for communicating with the server
type Contact interface {
	Listen(key string, udp string, http string, profile string) 
}

//CommunicationChannels contains the contact implementations
var CommunicationChannels = map[string]Contact{}