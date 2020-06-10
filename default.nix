{ pkgs ? import <nixpkgs> {} }:

let
  pyPkgs = python-packages: with python-packages; [ pygame ];
  python = pkgs.python2.withPackages pyPkgs;
in pkgs.writeScriptBin "wabble" ''
   ${python}/bin/python ${./.}/run_game_no_audio.py
''
