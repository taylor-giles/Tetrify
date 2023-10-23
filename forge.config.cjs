module.exports = {
  packagerConfig: {
    asar: true,
    extraResource: [
      "./engine"
    ],
    icon: './ui/public/favicon'
  },
  rebuildConfig: {},
  makers: [
    {
      name: '@electron-forge/maker-squirrel',
      config: {
        exe: 'Tetrify.exe',
        name: 'Tetrify'
      },
    },
    {
      name: '@electron-forge/maker-zip',
      platforms: ['linux', 'darwin'],
    },
    {
      name: '@electron-forge/maker-deb',
      config: {},
    },
    {
      name: '@electron-forge/maker-rpm',
      config: {},
    },
  ],
  plugins: [
    {
      name: '@electron-forge/plugin-auto-unpack-natives',
      config: {},
    },
  ],
};
