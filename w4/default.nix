{
  perSystem = { pkgs, ... }: {
    devShells.w4 = pkgs.callPackage ./shell.nix { inherit pkgs; };
  };
}
