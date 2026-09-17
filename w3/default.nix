{
  perSystem = { pkgs, ... }: {
    devShells.w3 = pkgs.callPackage ./shell.nix { inherit pkgs; };
  };
}
