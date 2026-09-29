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
        ];

        mostRecentWorkshop = builtins.head (
          builtins.sort (a: b: !builtins.lessThan a b) (map builtins.baseNameOf imports)
        );
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
