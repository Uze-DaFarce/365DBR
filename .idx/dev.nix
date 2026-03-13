{ pkgs, ... }: {
	# https://firebase.google.com/docs/studio/customize-workspace
	channel = "stable-23.11"; # or "unstable"
	packages = [
		pkgs.git
		pkgs.zip
		pkgs.nodejs
		pkgs.pnpm
	];
	# https://firebase.google.com/docs/studio/customize-workspace#environment-variables
	# env = {
	#   GREETING = "Hello, world!";
	# };
	# https://firebase.google.com/docs/studio/customize-workspace#user-services
	# services.http-server = {
	#   start = "npx http-server -p 8000";
	#   port = 8000;
	#   # availability = "private";
	# };
}
