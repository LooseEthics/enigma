# Enigma

This is an emulation of the Enigma encryption machine used by WW2 Germany. Not historically accurate.

Input character is first encrypted through the encryption rotors, then the wireboard, reflected, through the wireboard again
	and finally through the rotors in reverse order.

Settings file allows users to specify 4 facets of the machine: list of legal characters, number of encryption rotors, 
	initial positions of encryption rotors, and wireboard setup.

First line of settings contains legal characters. Their number serves as basis for generating internal rotor wiring.
	Redundant characters will be skipped. All plaintext characters must be contained here.
	It is a string.

Second line contains the total number of distinct rotors used during the encryption process.
	It is a single integer. It can be arbitrarily large, at least in theory.

Third line contains initial positions of rotors. This position is incremented once per character pass. This gives
	encryption pattern periodicity of c^n, where c is number of legal characters and n is number of rotors.
	It is a list of integers separated by commas (,). If the number of integers here is less than the number of rotors,
	the remainder will be set to 0 by default. Positions greater than legal will be reduced to fit.

Fourth line contains wireboard pairs which connect 2 distinct characters. Multiplicity is not allowed and causes 
	the program to terminate. Wireboard is an optional component of the machine.
	Pairs are separated by a comma (,). Integers within a pair are separated by a dash (-). These integers must be 
	less than the number of legal characters.

Available commands:

	e, enigma	initializes an enigma machine
	m, msg		loads and encrypts plaintext
	p, print	prints current ciphertext
	q, quit		quits the program
	w, write	write current ciphertext to file

Default file aliases:

	Settings file:
		<d>	enigmasettings.txt
	Input file:
		<d>	enigmaplain.txt
		<o>	enigmaout.txt
	Output file:
		<d>	enigmaout.txt
