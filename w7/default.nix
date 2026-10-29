{
  perSystem = { pkgs, ... }: {
    devShells.w7 = pkgs.callPackage ./shell.nix { inherit pkgs; };
  };
}
