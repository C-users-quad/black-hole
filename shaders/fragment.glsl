#version 430

in vec2 uv;
out vec4 fragColor;

uniform sampler2D tex;  // the output of your compute shader

void main() {
    fragColor = texture(tex, uv);
}
