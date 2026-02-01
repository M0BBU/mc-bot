{
  description = "Build environment for mc-bot";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };
  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem
      (system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
        in
          with pkgs;
          {
            devShells.default = mkShell {
              buildInputs = [
                python3
                uv
              ];
            };
          }
      );
}
