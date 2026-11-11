{
  description = "Description for the project";

  inputs = {
    flake-parts.url = "github:hercules-ci/flake-parts";
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs =
    inputs@{ flake-parts, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } (
      let
        imports = [
          ./w1
          ./w2
          ./w3
          ./w4
          ./w5
          ./w7
          ./w9
          ./w10
        ];

        mostRecentWorkshop = let
          names = (map builtins.baseNameOf imports);
          values = builtins.listToAttrs (map (name: { inherit name; value = builtins.fromJSON (builtins.substring 1 (-1) name); }) names);
          sorted = builtins.sort (a: b: !builtins.lessThan values.${a} values.${b}) names;
        in builtins.head sorted;
      in
      {
        inherit imports;
        systems = [
          "x86_64-linux"
          "aarch64-linux"
          "aarch64-darwin"
        ];
        perSystem = { self', ... }: {
          devShells.default = self'.devShells.${mostRecentWorkshop};
        };
      }
    );
}
