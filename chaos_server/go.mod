module chaos_server

go 1.16

replace sieve.client => ../sieve_client

require (
	k8s.io/apimachinery v0.18.9 // indirect
	sieve.client v0.0.0-00010101000000-000000000000
)
