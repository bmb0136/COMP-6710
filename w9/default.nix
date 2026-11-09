{
  perSystem = { pkgs, ... }: {
    devShells.w9 = pkgs.callPackage ./shell.nix { inherit pkgs; };
  };
}
