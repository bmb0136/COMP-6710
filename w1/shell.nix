{
  pkgs ? import <nixpkgs> { },
  ...
}:
pkgs.mkShell {
  packages = [
    (pkgs.python3.withPackages (pp: [ pp.scipy pp.numpy ]))
  ];
}
