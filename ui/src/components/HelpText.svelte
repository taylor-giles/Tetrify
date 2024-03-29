<script>
    import { IS_ELECTRON } from "../../../engine/engineUtils";
</script>

<main>
    <h2>Welcome to Tetrify!</h2>
    <p>
        This app provides an easy and intuitive interface for converting custom
        drawings into animations of falling Tetriminoes. It uses an optimized
        semi-random approach for generating animations, by simulating many
        possible sequences of block positions to find a matching board state.
        Read the following guide for instructions on using this app and
        descriptions of the options and processes involved.
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
        Keep in mind that not all images can be Tetrified exactly, but close
        approximations can be made. For more details, see "Simulation Options".
    </p>

    {#if !IS_ELECTRON}
        <p>
            <b>
                ⚠️ All simulations run from the web app are limited to one
                thread and a runtime of at most 5 minutes.
            </b>
            <br /> As many simulations will not be able to reach completion
            given these limitations, it is recommended to
            <a
                href="https://github.com/taylor-giles/Tetrify#installation"
                target="_blank"
                rel="noreferrer noopener"
            >
                install the Electron app</a
            >, which leverages local hardware and allows for unlimited runtime.
        </p>
    {/if}

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
        through some compromises. Use the following guide to better understand
        why some images are not "Tetrify-able" and how to use these options to
        work around those restrictions:
    </p>
    <ul>
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
            animations in which blocks are allowed to remain floating, at the cost
            of increased runtime. Disable this option if your drawing includes floating
            blocks.
        </li>
        <li>
            <b>Reduce Wells & Towers</b> - In animations made from large drawings,
            it is common to see many I-blocks stacked on top of each other. Enabling
            this option will instruct the simulation to avoid making any wells or
            towers, which subsequently reduces the number of excess I-blocks used.
            However, the addition of these features can increase runtime of large
            or complicated drawings. Enable this if you notice excessive I-blocks
            in your animations.
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
    </ul>
    <h3>TIPS</h3>
    <p>Here are some tips to help you get the most out of Tetrify:</p>
    <ul>
        <li>
            When possible, try to make sure that the number of cells in each
            part of your drawing is a multiple of four. This ensures that the
            simulation does not fail immediately without false
            positives/negatives.
        </li>
        <li>
            If your drawing does not have any "floating" parts, put it at the
            bottom of the canvas, and keep the "Enforce Gravity" option enabled.
            This will reduce unnecessary computation & runtime.
        </li>
        <li>
            Keep the canvas as small as possible for your drawing. Increasing
            the canvas size increases runtime.
        </li>
    </ul>
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
    ul {
        list-style: inside;
        padding-left: 0;
    }
</style>
