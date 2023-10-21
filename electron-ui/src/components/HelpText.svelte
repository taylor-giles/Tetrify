<main>
    <h2>Welcome to Tetrify!</h2>
    <p>
        This app provides an easy and intuitive interface for converting custom
        drawings into animations of falling Tetriminoes. It uses an optimized
        semi-random approach for generating animations, by simulating many
        possible sequences of block positions to find a matching board state.
        Read this guide for instructions on using this app and descriptions of
        the options and processes involved.
    </p>

    <h3>QUICK START</h3>
    <p>
        To use this app as-is, simply click and drag in the canvas on the left
        to draw the image you would like to Tetrify, then press "Animate!". The
        app will run simulations to find animations that match your drawing.
        Animations are shown in the preview window as they are generated, so you
        can stop the simulation whenever you see one you like. You can then view
        the animations and the images they produce, and save what you like.
    </p>
    <p>
        Keep in mind that some drawings cannot be Tetrified without making
        changes to the simulation. For more details, see "Simulation Options".
    </p>

    <h3>Drawing</h3>
    <p>
        Click and drag in the canvas on the left to draw the desired end-goal
        image (black cells are background, and white cells are part of the image
        to Tetrify). The size of the canvas can be changed using the Canvas
        Height and Canvas Width options on the right, but note that the canvas
        will be cleared whenever it is resized. If you want to start over at any
        point, the "Clear" button will reset the canvas back to the default
        blank state.
    </p>
    <p>
        When you're satisfied, press the "Animate!" button, and the simulator
        will begin looking for valid ways to Tetrify your artwork.<br />
    </p>

    <h3>Viewing Results & Customization</h3>
    <p>
        As valid animations are simulated, they will appear in the preview
        window. You can customize the appearance of the animations using the
        Block Colors and Display Options settings on the right. If multiple
        valid animations are found, you can use the buttons at the bottom of the
        preview window to see them all. To see only the final "Tetrified" image,
        toggle on the "Show Only Final Board State" option.
    </p>
    <p>
        It is important to note that for some drawings, it may take a very long
        time to fully simulate all animation possibilities. Therefore, it is
        recommended to interrupt the simulation by pressing "Stop" once
        satisfied with the generated animations.
    </p>

    <h3>Simulation Options</h3>
    <p>
        Some images are not "Tetrify-able" using the default settings, for
        various reasons. The Simulation Options on the right are designed to
        offer greater flexibility, allowing the simulation to "bend the rules"
        in certain ways to make it possible to Tetrify a wider range of images,
        through some compromises. Use this guide to better understand why some
        images are not "Tetrify-able" and how to use these options to work
        around those restrictions:
        <li>
            <b>False Positives</b> - The maximum number of extra cells that the animation
            is "allowed" to fill with blocks. For example, an image consisting of
            exactly three cells in a line would not be "Tetrify-able", because there
            is no Tetrimino that consists of only three cells. However, allowing
            at least one "false positive" would mean that an extra background cell
            could be filled, and an animation could be generated. In general, increasing
            this value will increase the likelihood that an animation will be found,
            while sacrificing image integrity.
        </li>
        <li>
            <b>False Negatives</b> - The maximum number of image cells that the animation
            is "allowed" to omit. For example, an image consisting of exactly five
            cells in a line would not be "Tetrify-able", because there is no way
            to fill exactly five cells with Tetriminoes. However, allowing at least
            one "false negative" would mean that the extra cell could be left as
            background, and an animation could be generated. In general, increasing
            this value will increase the likelihood that an animation will be found,
            while sacrificing image integrity.
        </li>
        <li>
            <b>Enforce Gravity</b> - If this option is enabled, then all blocks in
            the simulation must fall until landing on the bottom of the canvas or
            another block. However, by disabling this option, it is possible to create
            animations in which blocks are allowed to remain floating - in this case,
            the blocks will fall until they either reach the desired location or
            land on another block, then stop. In general, disabling this option will
            increase the likelihood that an animation will be found, but simulation
            time will also increase.
        </li>
        <li>
            <b>Number of Threads</b> - Since this app's simulations involve randomized
            elements, running multiple simulations at the same time can result in
            finding multiple different animations more quickly. This option allows
            you to specify how many distinct threads should be used to run simulations.
            Note that this value cannot exceed the number of available CPU threads,
            and that increasing this value can result in high CPU usage.
        </li>
        <li>
            <b>Remove Duplicates</b> - It is possible that the simulation may encounter
            animations with identical final states or, if using multiple threads,
            identical animations. If this option is enabled, animations with end-states
            that have already been seen in previously-generated animations will not
            be saved or shown.
        </li>
    </p>
</main>

<style>
    main {
        padding-bottom: 20px;
    }
    h3 {
        margin-bottom: -15px;
        margin-top: 35px;
    }
    p {
        margin-bottom: -10px;
    }
    li {
        margin-top: 8px;
    }
</style>
