{
  perSystem = { pkgs, ... }: {
    devShells.w1 = pkgs.callPackage ./shell.nix { inherit pkgs; };
  };
}
