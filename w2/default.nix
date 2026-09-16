{
  perSystem = { pkgs, ... }: {
    devShells.w2 = pkgs.callPackage ./shell.nix { inherit pkgs; };
  };
}
