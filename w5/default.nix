{
  perSystem = { pkgs, ... }: {
    devShells.w5 = pkgs.callPackage ./shell.nix { inherit pkgs; };
  };
}
