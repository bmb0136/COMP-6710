{
  perSystem = { pkgs, ... }: {
    devShells.w10 = pkgs.callPackage ./shell.nix { inherit pkgs; };
  };
}
